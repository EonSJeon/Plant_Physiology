import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
from matplotlib.widgets import Button
import numpy as np
from enum import Enum

def findIdxOf(val, arr):
    return np.argmin(np.abs(arr - val))

class ToolbarMode(Enum):
    PAN_ZOOM = 'pan/zoom'
    ZOOM_RECT = 'zoom rect'
    ACTIVE = ''


class UI():
    def __init__(self, recorder):
        
        self.parent=recorder
        
        self.paused=False
        self.max_len = 10000000
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        
        self.t_max_width=500
        self.y_max_width=2e4
        
        self.display_ts = np.zeros(self.max_len)
        self.display_ys = np.zeros(self.max_len)
        
        self.click_count=0
        
        self.start_line=None
        self.end_line=None
        self.poly=None
        
        self.ax.set_xlim([-self.t_max_width,0])
        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=1, cache_frame_data=False)
        
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.prev_x_lim = self.ax.get_xlim()
        self.prev_y_lim = self.ax.get_ylim()
        
        # Connect to axes limit change events
        self.ax.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.ax.callbacks.connect('ylim_changed', self.on_ylim_changed)
        

        self.ax.set_title("Project Hashirama: Time vs Voltage")
        self.ax.set_xlabel("Time [ms]")
        self.ax.set_ylabel("Voltage [mV]")
        
        ax_button = plt.axes([0.81, 0.05, 0.1, 0.075])  # Adjust these dimensions as needed
        self.btn_save = Button(ax_button, 'Save')
        self.btn_save.on_clicked(self.parent.start_saving)
    
    def check_data_stream_form(self):
        
        if self.parent.data_stream.shape[0]<2:
                return None
        if self.parent.data_stream.shape[0] > self.max_len:  
            self.parent.data_stream = self.parent.data_stream[-self.max_len: ,:]
        return np.copy(self.parent.data_stream)

    def animate(self, i):
        if not self.paused:
            current_data_stream= self.check_data_stream_form()
            if current_data_stream is not None:
                current_data_stream[:, 0] -= current_data_stream[-1, 0]

                ctlimlow, ctlimhigh = self.ax.get_xlim()

                lowIdx = findIdxOf(ctlimlow, current_data_stream[:, 0])
                highIdx = findIdxOf(ctlimhigh, current_data_stream[:, 0])

                self.display_ts = current_data_stream[lowIdx:highIdx + 1, 0]
                self.display_ys = current_data_stream[lowIdx:highIdx + 1, 1]

                self.line.set_data(self.display_ts, self.display_ys)
                plt.draw()


        
    def autoscale(self):
        current_data_stream =self.check_data_stream_form()
        if current_data_stream is not None:
            current_ts=current_data_stream[:,0]
            current_ys=current_data_stream[:,1]
            
            amp_mean=np.mean(current_ys)
            current_ys-=amp_mean
            time_diff_s=(current_ts[-1]-current_ts[0])/len(current_ts)/1000

            fft_result = np.fft.fft(current_ys)
            fft_freq = np.fft.fftfreq(len(current_ys), d=time_diff_s)

            magnitude_spectrum = np.abs(fft_result)
            dominant_frequency_index = np.argmax(magnitude_spectrum[1:]) + 1
            dominant_frequency = np.abs(fft_freq[dominant_frequency_index])

            print(f"dom freq: {dominant_frequency} Hz")
            
            if dominant_frequency > 0:
                cycle_time = 1 / dominant_frequency  # Cycle time in seconds
                horizontal_span = 3.5 * cycle_time
            else:
                # Convert the entire time range from ms to s for horizontal span
                horizontal_span = time_diff_s
                
            vertical_span = (max(current_ys) - min(current_ys)) / 2  # Half span for setting ylim
            
            # Apply calculated scales to axes
            # Assuming the latest data point is at temp_sampled_t[-1], convert this to seconds
            
            self.ax.set_xlim(- 2 * horizontal_span * 1000,  - horizontal_span * 1000)  # Convert back to ms for xlim
            self.ax.set_ylim(amp_mean - vertical_span*1.5, amp_mean + vertical_span*1.5)

        
        
    def on_key_press(self, event):
        if event.key == 'ctrl+a':
            self.autoscale()
            plt.draw()
        elif event.key ==' ':
            if self.paused:
                self.erase_marks()
            self.paused=not self.paused
        elif event.key == 'ctrl+alt+s':
            if self.paused and self.poly is not None:
                start_line_t=self.start_line.get_xdata()[0]
                end_line_t=self.end_line.get_xdata()[0]
                
                start_index = findIdxOf(start_line_t,self.display_ts)
                end_index = findIdxOf(end_line_t,self.display_ts)
                
                save_t=self.display_ts[start_index:end_index+1]
                save_y=self.display_ys[start_index:end_index+1]
                
                self.parent.save(save_t,save_y)

            
    def on_scroll(self, event):
        if self.toolbar_mode() != ToolbarMode.ACTIVE:
            xdata, ydata = event.xdata, event.ydata  
            if not xdata or not ydata: 
                return
            
            base_scale = 1.1
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                return

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor


            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
            
            self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
            self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])

            plt.draw()
    
    def on_click(self, event):
        if self.paused:
            if event.button==1 and event.inaxes is not None:
                if self.click_count==0:
                    self.erase_marks()
                    self.start_line = self.ax.axvline(x=event.xdata, color='red')
                    self.click_count=1
                elif self.click_count==1:
                    start_line_t=self.start_line.get_xdata()[0]
                    if(event.xdata>start_line_t):
                        end_line_t=event.xdata
                        self.end_line = self.ax.axvline(x=end_line_t, color='blue')
                        self.poly = Polygon([(start_line_t,  self.y_max_width), \
                                                (start_line_t, -self.y_max_width), \
                                                (  end_line_t, -self.y_max_width), \
                                                (  end_line_t,  self.y_max_width)], 
                                                color='0.9', alpha=0.5)
                        self.ax.add_patch(self.poly)
                        self.click_count=0
                    else:
                        self.erase_marks()
                        self.start_line = self.ax.axvline(x=event.xdata, color='red')
                else:
                    print(f"Something Error: self.click_count({self.click_count}) exceeds two.")
                    return
                self.fig.canvas.draw()
            else:
                print('Clicked outside axes bounds but inside plot window')

    

    def erase_marks(self):
        if self.start_line is not None:
            self.start_line.remove()
            del self.start_line
            self.start_line=None
        if self. end_line is not None:
            self.end_line.remove()
            del self.end_line
            self.end_line=None
        if self.poly is not None:
            self.poly.remove()
            del self.poly
            self.poly=None
            
    

    def on_xlim_changed(self, event=None):
        
        current_t_lim = self.ax.get_xlim()
        w = current_t_lim[1] - current_t_lim[0]  
        
        if w > self.t_max_width:
            w = self.t_max_width

        left_lim = max(current_t_lim[0], -self.t_max_width)
        right_lim = min(left_lim + w, 0)

        if (left_lim, right_lim) != current_t_lim:
            self.ax.set_xlim([left_lim, right_lim])
        else:
            self.prev_x_lim = current_t_lim

    def on_ylim_changed(self, event=None):
        
        current_y_lim = self.ax.get_ylim()
        h = current_y_lim[1] - current_y_lim[0]
        
        if h > self.y_max_width:
            h = self.y_max_width

        bottom_lim = max(current_y_lim[0], -self.y_max_width/2)

        if bottom_lim + h > self.y_max_width/2:
            bottom_lim = self.y_max_width/2 - h

        top_lim = bottom_lim + h

        if (bottom_lim, top_lim) != current_y_lim:
            self.ax.set_ylim([bottom_lim, top_lim])
        else:
            self.prev_y_lim = current_y_lim
    
    
    def toolbar_mode(self):
        # This function checks the toolbar mode for figures with a toolbar
        toolbar = self.fig.canvas.toolbar
        if toolbar is not None:
            if toolbar.mode == ToolbarMode.PAN_ZOOM.value:
                return ToolbarMode.PAN_ZOOM
            elif toolbar.mode == ToolbarMode.ZOOM_RECT.value:
                return ToolbarMode.ZOOM_RECT
            else:
                return ToolbarMode.ACTIVE


    